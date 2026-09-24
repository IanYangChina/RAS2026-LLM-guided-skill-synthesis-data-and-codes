## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3300 | 0.00 | ❌ rejected |
| 0 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 0 | 0.8773 | 0.88 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `91e4de206df15f80750cdb645e4a7fbeecac222f6e7e3c9e7aabeca93992a5f5`
- Frozen task target: [0.6761612134249316, -0.02015088565858767, 0.15]
- Goal object position: (0.6761612134249316, -0.02015088565858767, 0.15)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.35, 0.0, 0.32)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.35, 0, 0.32]
objects:
  - name: obstacle_block
    role: obstacle
    dynamics: static
    geometry: box
    dimensions_m: [0.08, 0.3, 0.3]
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_task_target: [0.6762, -0.0202, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.6761612134249316, -0.02015088565858767, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 91e4de206df15f80750cdb645e4a7fbeecac222f6e7e3c9e7aabeca93992a5f5

## Current Skill (Q=-0.330) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.17
    tolerance: 0.02
    orientation:
      mode: keep_current
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.17], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.330
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 0.00 | 0.2187 |
| descend_1 | 0.00 | 0.67 | 0.0814 |
| fine_approach | 0.00 | 1.00 | 0.0986 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.567, -0.012, 0.301) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.709→0.709 | 0.00 / 0.000 | 0.000 | 4470.254 | link7 ↔ obstacle_block/obstacle_block_geom |
| descend_1 | descend | 0.00 / step_budget | (0.567, -0.012, 0.301)→(0.560, -0.011, 0.225) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.709→0.709 | 0.67 / 0.667 | 203.724 | 1662.432 | link5 ↔ obstacle_block/obstacle_block_geom |
| fine_approach | descend | 0.00 / step_budget | (0.560, -0.011, 0.225)→(0.614, -0.041, 0.243) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.709→0.709 | 1.00 / 1.333 | 265.740 | 1656.945 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.392
- path_efficiency: 0.287
- arc_smoothness: 0.966
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 9785.444 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.183
- min_tcp_distance: 0.122
- tcp_proximity_score: 0.296
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link6
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.330
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.274


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f800b324b333bf92ab38395ea2012437ea47aa487cfa00211f655ffc1e1f3195`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3279d67c4edbf0c030d9541a1fc5a04a28b1fb39645a052c44a102acb501fa91`; realized-scene SHA-256: `91e4de206df15f80750cdb645e4a7fbeecac222f6e7e3c9e7aabeca93992a5f5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.67616,-0.02015,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.67616,-0.02015,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.35294,"average_mean_iterations":77.80882,"average_solve_count":68.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.height_offset":0.20965,"approach_1.speed":0.31672,"descend_1.descend_speed":0.31664,"descend_1.descend_tolerance":0.00842,"fine_approach.fine_speed":0.11328,"fine_approach.fine_tolerance":0.00409},"optimized_scores":{"best_composite_score":-0.33,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":254.0,"contact_point_centroid":[0.52067,-0.00599,0.29956],"force_p95":7093.81542,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":9785.444,"mean_force":989.27523,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4344,-0.00375,0.37249]},{"body_a":"obstacle_block","body_b":"link7","contact_count":87.0,"contact_point_centroid":[0.49198,-0.0052,0.29849],"force_p95":8916.58343,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":9534.427,"mean_force":2283.05232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44871,-0.00649,0.33097]},{"body_a":"obstacle_block","body_b":"link5","contact_count":268.0,"contact_point_centroid":[0.53834,0.07074,0.29937],"force_p95":896.16056,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":2332.2661,"mean_force":394.89986,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56079,-0.01026,0.21828]},{"body_a":"obstacle_block","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.53852,-0.09931,0.26321],"force_p95":1474.32533,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1953.79469,"mean_force":551.56591,"phase_index":2.0,"phase_name":"fine_approach","phase_type":"descend","tcp_position_centroid":[0.55818,-0.07761,0.25156]},{"body_a":"obstacle_block","body_b":"link5","contact_count":178.0,"contact_point_centroid":[0.53176,0.03751,0.29976],"force_p95":884.94239,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1395.51266,"mean_force":413.79171,"phase_index":2.0,"phase_name":"fine_approach","phase_type":"descend","tcp_position_centroid":[0.56258,0.00406,0.2133]},{"body_a":"obstacle_block","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.53965,-0.01864,0.22306],"force_p95":833.10756,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":959.89351,"mean_force":410.91083,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55156,-0.01387,0.25005]}],"total_contact_groups":6},"final_pose_error":0.18254,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.58187,-0.07578,0.29606],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":9785.444,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":442.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":9785.444,"phase_type":"approach","raw_contact_event_count":341.0,"raw_peak_contact_force":9785.444,"tcp_end":[0.5596,-0.01481,0.31902],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.64432,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":306.55907,"phase_name":"descend_1","phase_peak_obstacle_force":2332.2661,"phase_type":"descend","raw_contact_event_count":350.0,"raw_peak_contact_force":2332.2661,"tcp_end":[0.54747,-0.01273,0.19443],"tcp_start":[0.5596,-0.01481,0.31902],"tcp_to_object_dist_end":0.58111,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":235.46493,"phase_name":"fine_approach","phase_peak_obstacle_force":1953.79469,"phase_type":"descend","raw_contact_event_count":211.0,"raw_peak_contact_force":1953.79469,"tcp_end":[0.58187,-0.07578,0.29606],"tcp_start":[0.54747,-0.01273,0.19443],"tcp_to_object_dist_end":0.65724,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `66d26d1c2bdf955217f340b9b03f23361c9eeea750a84bd79880abed4fe043dd`; realized-scene SHA-256: `09b1e5e25d1c1085fb3b7b529543c8c0ed19e559c3b72845a3b8c8c62899d8b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.65856,-0.02632,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.65856,-0.02632,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":21.0,"average_failure_rate":0.32308,"average_mean_iterations":70.24615,"average_solve_count":65.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.height_offset":0.15066,"approach_1.speed":0.29985,"descend_1.descend_speed":0.3093,"descend_1.descend_tolerance":0.01374,"fine_approach.fine_speed":0.11963,"fine_approach.fine_tolerance":0.00568},"optimized_scores":{"best_composite_score":-0.33,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.49228,-0.00746,0.29909],"force_p95":1104.61811,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1813.64576,"mean_force":369.97829,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45341,-0.00927,0.33345]},{"body_a":"obstacle_block","body_b":"link5","contact_count":355.0,"contact_point_centroid":[0.53979,0.06625,0.29949],"force_p95":849.88347,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1457.30515,"mean_force":369.74736,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55594,-0.03084,0.22177]},{"body_a":"obstacle_block","body_b":"link5","contact_count":142.0,"contact_point_centroid":[0.52843,0.01211,0.29974],"force_p95":823.61268,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1369.64801,"mean_force":417.71364,"phase_index":2.0,"phase_name":"fine_approach","phase_type":"descend","tcp_position_centroid":[0.56532,-0.01645,0.21474]},{"body_a":"obstacle_block","body_b":"link6","contact_count":231.0,"contact_point_centroid":[0.52782,-0.00993,0.29968],"force_p95":539.209,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1082.56899,"mean_force":329.13002,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44151,-0.00674,0.37857]},{"body_a":"obstacle_block","body_b":"link7","contact_count":100.0,"contact_point_centroid":[0.53979,-0.05835,0.19677],"force_p95":353.32825,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":472.56843,"mean_force":204.0343,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54177,-0.039,0.21189]},{"body_a":"obstacle_block","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.53977,0.0008,0.16932],"force_p95":396.21582,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":457.4208,"mean_force":275.27838,"phase_index":2.0,"phase_name":"fine_approach","phase_type":"descend","tcp_position_centroid":[0.5485,-0.00916,0.19638]}],"total_contact_groups":6},"final_pose_error":0.11545,"key_states":{"actual_goal_position":[0.65856,-0.02632,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.58901,-0.04113,0.24095],"realised_goal_position":[0.65856,-0.02632,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1813.64576,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":451.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":1813.64576,"phase_type":"approach","raw_contact_event_count":319.0,"raw_peak_contact_force":1813.64576,"tcp_end":[0.56927,-0.02043,0.27908],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.63432,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":304.61361,"phase_name":"descend_1","phase_peak_obstacle_force":1457.30515,"phase_type":"descend","raw_contact_event_count":455.0,"raw_peak_contact_force":1457.30515,"tcp_end":[0.54343,-0.04138,0.21122],"tcp_start":[0.56927,-0.02043,0.27908],"tcp_to_object_dist_end":0.5845,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":213.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":221.76333,"phase_name":"fine_approach","phase_peak_obstacle_force":1369.64801,"phase_type":"descend","raw_contact_event_count":215.0,"raw_peak_contact_force":1369.64801,"tcp_end":[0.58901,-0.04113,0.24095],"tcp_start":[0.54343,-0.04138,0.21122],"tcp_to_object_dist_end":0.63772,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b7b048f5d0b9db8e06f7a4e7cd38174b92fd1a59140bfe1012f881edd44f4223`; realized-scene SHA-256: `f04b195e402ac39779662418f5ff4bea89ac7f3f52518881a8eb9756a965f187`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.74431,0.00113,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.74431,0.00113,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":27.0,"average_failure_rate":0.32143,"average_mean_iterations":69.25,"average_solve_count":84.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.height_offset":0.16318,"approach_1.speed":0.35898,"descend_1.descend_speed":0.36009,"descend_1.descend_tolerance":0.01299,"fine_approach.fine_speed":0.1002,"fine_approach.fine_tolerance":0.00569},"optimized_scores":{"best_composite_score":-0.33,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.4887,0.00297,0.29905],"force_p95":1147.3015,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1811.67345,"mean_force":399.65274,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44763,0.00037,0.33215]},{"body_a":"obstacle_block","body_b":"link5","contact_count":831.0,"contact_point_centroid":[0.53712,0.11846,0.29987],"force_p95":703.3519,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1647.39307,"mean_force":355.47313,"phase_index":2.0,"phase_name":"fine_approach","phase_type":"descend","tcp_position_centroid":[0.58011,-0.00244,0.21222]},{"body_a":"obstacle_block","body_b":"link5","contact_count":58.0,"contact_point_centroid":[0.53965,0.04922,0.29879],"force_p95":842.27221,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1197.72517,"mean_force":247.72199,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56798,0.00135,0.22902]},{"body_a":"obstacle_block","body_b":"link6","contact_count":183.0,"contact_point_centroid":[0.5273,-0.00348,0.29962],"force_p95":621.58365,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1113.02757,"mean_force":331.82885,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43964,0.00038,0.37417]},{"body_a":"obstacle_block","body_b":"link7","contact_count":215.0,"contact_point_centroid":[0.53985,-0.00907,0.22356],"force_p95":339.78141,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":371.08778,"mean_force":241.43488,"phase_index":2.0,"phase_name":"fine_approach","phase_type":"descend","tcp_position_centroid":[0.54238,-0.00354,0.20719]}],"total_contact_groups":5},"final_pose_error":0.0837,"key_states":{"actual_goal_position":[0.74431,0.00113,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.67191,-0.00677,0.19127],"realised_goal_position":[0.74431,0.00113,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1811.67345,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":387.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":1811.67345,"phase_type":"approach","raw_contact_event_count":268.0,"raw_peak_contact_force":1811.67345,"tcp_end":[0.57204,0.00069,0.3047],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.64813,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":1197.72517,"phase_type":"descend","raw_contact_event_count":58.0,"raw_peak_contact_force":1197.72517,"tcp_end":[0.59045,0.02042,0.27071],"tcp_start":[0.57204,0.00069,0.3047],"tcp_to_object_dist_end":0.64987,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":339.99096,"phase_name":"fine_approach","phase_peak_obstacle_force":1647.39307,"phase_type":"descend","raw_contact_event_count":1046.0,"raw_peak_contact_force":1647.39307,"tcp_end":[0.67191,-0.00677,0.19127],"tcp_start":[0.59045,0.02042,0.27071],"tcp_to_object_dist_end":0.69864,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```