## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.0720 | 0.31 | ❌ rejected |
| 7 | approach → descend → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5422 | 0.92 | ✅ accepted |
| 6 | approach → descend → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6262 | 0.91 | ❌ rejected |
| 5 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | -0.2500 | 0.00 | ❌ rejected |
| 4 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.6472 | 0.90 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`
- Frozen task target: [0.7125095466604666, 0.039721380096957554, 0.15]
- Goal object position: (0.7125095466604666, 0.039721380096957554, 0.15)
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
  frozen_task_target: [0.7125, 0.0397, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7125095466604666, 0.039721380096957554, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2

## Current Skill (Q=-0.072) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: approach_high_side
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    approach_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.04
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed_approach:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_side
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed_descend:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: lateral_approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lateral_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.02
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed_lateral:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high_side** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed_approach: status=consumed; consumers=generator.speed (replace)
- **descend_side** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed_descend: status=consumed; consumers=generator.speed (replace)
- **lateral_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed_lateral: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.072
- **task_score** (E): 0.308
- **fitness_score**: 0.308  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high_side | 1.00 | 0.33 | 0.3929 |
| descend_side | 1.00 | 0.33 | 0.0199 |
| lateral_approach | 1.00 | 0.67 | 0.0059 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_high_side | approach | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.718, 0.023, 0.189) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.33 / 0.333 | 84.345 | 86.185 | link5 ↔ obstacle_block/obstacle_block_geom |
| descend_side | descend | 1.00 / step_budget | (0.718, 0.023, 0.189)→(0.714, 0.023, 0.169) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.33 / 0.333 | 56.265 | 86.656 | link5 ↔ obstacle_block/obstacle_block_geom |
| lateral_approach | approach | 1.00 / step_budget | (0.714, 0.023, 0.169)→(0.714, 0.023, 0.164) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.67 / 0.667 | 116.022 | 134.251 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.766
- path_efficiency: 0.662
- arc_smoothness: 0.994
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.012
- min_tcp_distance: 0.012
- tcp_proximity_score: 0.924
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.924
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.924
- **Median Q (composite search score)**: -0.380
- **K-run variance**: 0.1897
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.0
- **Final σ (mean)**: 0.264


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ee3df1cfa385834280b1b81fd9f0e349b6eb2ac9615126fa1df028e39d9bc447`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c0103a17499c8e8b9aa43b2853a2df398616901e8934c1ef10fa47d87723b50d`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5974,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high_side.approach_tolerance":0.04225,"approach_high_side.arc_height":0.20829,"approach_high_side.speed_approach":0.07142,"descend_side.descend_tolerance":0.01469,"descend_side.speed_descend":0.07889,"lateral_approach.lateral_tolerance":0.01214,"lateral_approach.speed_lateral":0.10538},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":27.0,"contact_point_centroid":[0.53986,0.12864,0.29984],"force_p95":211.03565,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":215.31139,"mean_force":178.85155,"phase_index":2.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.71422,0.04028,0.16521]}],"total_contact_groups":1},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.715,0.04075,0.16472],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":215.31139,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71907,0.04039,0.18924],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.74465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.7149,0.03999,0.16963],"tcp_start":[0.71907,0.04039,0.18924],"tcp_to_object_dist_end":0.73583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":192.45632,"phase_name":"lateral_approach","phase_peak_obstacle_force":215.31139,"phase_type":"approach","raw_contact_event_count":27.0,"raw_peak_contact_force":215.31139,"tcp_end":[0.715,0.04075,0.16472],"tcp_start":[0.7149,0.03999,0.16963],"tcp_to_object_dist_end":0.73486,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5aed51a381cd066930e6976e6d6ccfd73886636bec948604cbfe8eb976a9a4c5`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09649,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high_side.approach_tolerance":0.02916,"approach_high_side.arc_height":0.18711,"approach_high_side.speed_approach":0.10439,"descend_side.descend_tolerance":0.02436,"descend_side.speed_descend":0.12621,"lateral_approach.lateral_tolerance":0.01361,"lateral_approach.speed_lateral":0.1116},"optimized_scores":{"best_composite_score":-0.38,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":67.0,"contact_point_centroid":[0.53991,0.13791,0.29996],"force_p95":174.36947,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":259.96912,"mean_force":162.27781,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.68986,0.04951,0.17874]},{"body_a":"obstacle_block","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.53975,0.13881,0.29989],"force_p95":258.39419,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":258.55516,"mean_force":241.6385,"phase_index":0.0,"phase_name":"approach_high_side","phase_type":"approach","tcp_position_centroid":[0.69138,0.04998,0.19058]},{"body_a":"obstacle_block","body_b":"link5","contact_count":44.0,"contact_point_centroid":[0.53995,0.13099,0.29998],"force_p95":170.08119,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":187.44286,"mean_force":147.94864,"phase_index":2.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.68824,0.04923,0.16666]}],"total_contact_groups":3},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.68787,0.049,0.16396],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":259.96912,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":253.03462,"phase_name":"approach_high_side","phase_peak_obstacle_force":258.55516,"phase_type":"approach","raw_contact_event_count":5.0,"raw_peak_contact_force":258.55516,"tcp_end":[0.6911,0.04995,0.18851],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.71809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":79.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":168.7957,"phase_name":"descend_side","phase_peak_obstacle_force":259.96912,"phase_type":"descend","raw_contact_event_count":67.0,"raw_peak_contact_force":259.96912,"tcp_end":[0.6885,0.0494,0.16899],"tcp_start":[0.6911,0.04995,0.18851],"tcp_to_object_dist_end":0.71065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":47.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":155.611,"phase_name":"lateral_approach","phase_peak_obstacle_force":187.44286,"phase_type":"approach","raw_contact_event_count":44.0,"raw_peak_contact_force":187.44286,"tcp_end":[0.68787,0.049,0.16396],"tcp_start":[0.6885,0.0494,0.16899],"tcp_to_object_dist_end":0.70884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f024bcb71fae796c72f6d149639f1bf75bdc180037c5c08610261d31ea463257`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.73702,-0.02132,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.73702,-0.02132,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02804,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high_side.approach_tolerance":0.03512,"approach_high_side.arc_height":0.21211,"approach_high_side.speed_approach":0.12962,"descend_side.descend_tolerance":0.02584,"descend_side.speed_descend":0.09537,"lateral_approach.lateral_tolerance":0.01438,"lateral_approach.speed_lateral":0.10101},"optimized_scores":{"best_composite_score":0.54386,"best_fitness_score":0.92386,"best_task_score":0.92386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01188,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.73805,-0.02167,0.16183],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.74419,-0.02189,0.18877],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.76807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":30.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.73989,-0.02173,0.16918],"tcp_start":[0.74419,-0.02189,0.18877],"tcp_to_object_dist_end":0.75929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.73805,-0.02167,0.16183],"tcp_start":[0.73989,-0.02173,0.16918],"tcp_to_object_dist_end":0.7559,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```