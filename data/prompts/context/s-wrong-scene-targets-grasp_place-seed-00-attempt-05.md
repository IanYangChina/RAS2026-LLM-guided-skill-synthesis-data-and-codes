## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 12 | -0.4356 | 0.17 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1730 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.0513 | 0.17 | ❌ rejected |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1716 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5136961687321454, -0.02302132862361297, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5136961687321454, -0.02302132862361297, 0.03]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.436) — your mutation base

```yaml
skill: grasp_place
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: insert_2
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.436
- **task_score** (E): 0.171
- **fitness_score**: 0.314  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.0000 |
| descend_grasp | 1.00 | 1.00 | 0.2644 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.030) | 0.263→0.263 | 1.00 / 4.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.039) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 27.129 | 0.138 |
| grasp | grasp | 1.00 / step_budget | (0.493, 0.001, 0.039)→(0.485, 0.000, 0.030) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 41.667 | 0.165 | 0.252 |
| lift | lift | 0.00 / guard_failure | (0.485, 0.000, 0.030)→(0.485, 0.000, 0.030) | (0.497, 0.000, 0.025)→(0.497, 0.000, 0.025) | 0.266→0.266 | 1.00 / 41.667 | 0.276 | 0.276 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.195
- phase_score: 0.009
- phase_breakdown.reach_object_score: 0.029
- phase_breakdown.reach_goal_score: 0.000
- grasp_place_fitness: 0.326

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.326
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.195
- **Median Q (composite search score)**: -0.437
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_grasp.descend_z_offset
- **Final σ (mean)**: 0.335


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5541,0.15165,0.22199]},{"name":"goal","value":[0.5137,-0.02302,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94828,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_height":0.1555,"approach_goal.goal_approach_speed":0.04239,"approach_object.approach_height":0.17048,"approach_object.approach_speed":0.08553,"descend_grasp.descend_speed":0.04845,"descend_grasp.descend_z_offset":0.0,"descend_place.place_speed":0.05121,"descend_place.place_z_offset":0.01015,"grasp.grasp_force":12.08412,"lift.lift_height":0.21975,"lift.lift_speed":0.08799,"release.release_duration":0.61931},"optimized_scores":{"best_composite_score":-0.43687,"best_fitness_score":0.31313,"best_task_score":0.17081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51386,-0.02221,-0.00222],"force_p95":0.26092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2639,"mean_force":0.23236,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50007,-0.02159,0.02917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51375,-0.02273,-0.00213],"force_p95":0.1615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23941,"mean_force":0.13296,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50128,-0.02162,0.03048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.50079,-0.00239,0.03195],"force_p95":0.08064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14605,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5001,-0.0216,0.0292]},{"body_a":"world","body_b":"grasp_target","contact_count":3564.0,"contact_point_centroid":[0.5137,-0.02302,-0.00196],"force_p95":0.12598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50298,-0.01082,0.16779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.50075,-0.04061,0.03102],"force_p95":0.09673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10871,"mean_force":0.06825,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50007,-0.02159,0.02917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17.0,"contact_point_centroid":[0.50077,-0.00244,0.03189],"force_p95":0.10031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10807,"mean_force":0.07544,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50007,-0.02159,0.02917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5002.0,"contact_point_centroid":[0.50079,-0.04075,0.03105],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08629,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50011,-0.0216,0.02921]}],"total_contact_groups":7},"final_pose_error":0.21978,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.51358,-0.02163,0.02553],"final_tcp_position":[0.50005,-0.02159,0.02915],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.2639,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02996],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26271,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49976,-0.0,0.30082],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27219,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02996],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26271,"object_z_max":0.02996,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3564.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50832,-0.02175,0.03816],"tcp_start":[0.49976,-0.0,0.30082],"tcp_to_object_dist_end":0.01334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02163,0.02555],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26506,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1535,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.23941,"tcp_end":[0.50007,-0.02159,0.02917],"tcp_start":[0.50832,-0.02175,0.03816],"tcp_to_object_dist_end":0.014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51358,-0.02163,0.02553],"object_pos_start":[0.5136,-0.02163,0.02555],"object_to_goal_dist_end":0.26508,"object_to_goal_dist_start":0.26506,"object_z_max":0.02555,"peak_contact_force":0.2639,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41.0,"raw_peak_contact_force":0.2639,"tcp_end":[0.50005,-0.02159,0.02915],"tcp_start":[0.50007,-0.02159,0.02917],"tcp_to_object_dist_end":0.01401,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.56442,0.24486,0.14677]},{"name":"goal","value":[0.50118,0.04505,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_height":0.13409,"approach_goal.goal_approach_speed":0.10619,"approach_object.approach_height":0.1836,"approach_object.approach_speed":0.10083,"descend_grasp.descend_speed":0.05662,"descend_grasp.descend_z_offset":0.0,"descend_place.place_speed":0.0306,"descend_place.place_z_offset":0.00986,"grasp.grasp_force":13.12152,"lift.lift_height":0.18368,"lift.lift_speed":0.07985,"release.release_duration":0.66172},"optimized_scores":{"best_composite_score":-0.42372,"best_fitness_score":0.32628,"best_task_score":0.19537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50159,0.04348,-0.00247],"force_p95":0.29101,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29878,"mean_force":0.24701,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48857,0.04174,0.02968]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50132,0.04451,-0.0023],"force_p95":0.21064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29074,"mean_force":0.14533,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48975,0.04185,0.03093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3495.0,"contact_point_centroid":[0.49011,0.02246,0.03312],"force_p95":0.0952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17177,"mean_force":0.05938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48859,0.04175,0.02971]},{"body_a":"world","body_b":"grasp_target","contact_count":3564.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49709,0.02112,0.16756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.48852,0.06067,0.03219],"force_p95":0.10014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11722,"mean_force":0.06818,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48857,0.04174,0.02968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15.0,"contact_point_centroid":[0.49,0.02254,0.03289],"force_p95":0.10311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11403,"mean_force":0.08246,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48857,0.04174,0.02968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5464.0,"contact_point_centroid":[0.48855,0.061,0.03227],"force_p95":0.07964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08694,"mean_force":0.04239,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48861,0.04175,0.02973]}],"total_contact_groups":7},"final_pose_error":0.1837,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50114,0.042,0.02498],"final_tcp_position":[0.48855,0.04174,0.02966],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.29878,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02996],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.23994,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49976,-0.0,0.30082],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27458,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02996],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23994,"object_z_max":0.02996,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3564.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49663,0.0424,0.03828],"tcp_start":[0.49976,-0.0,0.30082],"tcp_to_object_dist_end":0.01335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.042,0.02501],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24491,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19098,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10759.0,"raw_peak_contact_force":0.29074,"tcp_end":[0.48857,0.04174,0.02968],"tcp_start":[0.49663,0.0424,0.03828],"tcp_to_object_dist_end":0.01342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50114,0.042,0.02498],"object_pos_start":[0.50115,0.042,0.02501],"object_to_goal_dist_end":0.24493,"object_to_goal_dist_start":0.24491,"object_z_max":0.02501,"peak_contact_force":0.29878,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40.0,"raw_peak_contact_force":0.29878,"tcp_end":[0.48855,0.04174,0.02966],"tcp_start":[0.48857,0.04174,0.02968],"tcp_to_object_dist_end":0.01343,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63142,0.15919,0.19002]},{"name":"goal","value":[0.47616,-0.02015,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94737,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_height":0.22245,"approach_goal.goal_approach_speed":0.05983,"approach_object.approach_height":0.20042,"approach_object.approach_speed":0.05464,"descend_grasp.descend_speed":0.04935,"descend_grasp.descend_z_offset":2e-05,"descend_place.place_speed":0.04706,"descend_place.place_z_offset":0.02312,"grasp.grasp_force":12.9072,"lift.lift_height":0.29142,"lift.lift_speed":0.06265,"release.release_duration":0.48627},"optimized_scores":{"best_composite_score":-0.44629,"best_fitness_score":0.30371,"best_task_score":0.14658},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47626,-0.01963,-0.0022],"force_p95":0.2622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26542,"mean_force":0.23612,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46528,-0.01887,0.03136]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.01996,-0.00212],"force_p95":0.15566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22511,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46641,-0.0189,0.03249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4789.0,"contact_point_centroid":[0.46546,0.00031,0.0333],"force_p95":0.07186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14476,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.01887,0.03139]},{"body_a":"world","body_b":"grasp_target","contact_count":3452.0,"contact_point_centroid":[0.47616,-0.02015,-0.00196],"force_p95":0.12631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48543,-0.00944,0.16844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.46545,-0.03802,0.03325],"force_p95":0.09606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10939,"mean_force":0.06898,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46528,-0.01887,0.03136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.46544,0.00026,0.03325],"force_p95":0.10072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10309,"mean_force":0.06891,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46528,-0.01887,0.03136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.46548,-0.03813,0.03329],"force_p95":0.07229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08522,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46531,-0.01887,0.03139]}],"total_contact_groups":7},"final_pose_error":0.29144,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47605,-0.01906,0.02556],"final_tcp_position":[0.46526,-0.01887,0.03134],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02996],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28616,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49976,-0.0,0.30082],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27263,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02996],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28616,"object_z_max":0.02996,"peak_contact_force":81.14225,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3452.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47309,-0.01902,0.03918],"tcp_start":[0.49976,-0.0,0.30082],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01906,0.02559],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28801,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15109,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11573.0,"raw_peak_contact_force":0.22511,"tcp_end":[0.46528,-0.01887,0.03136],"tcp_start":[0.47309,-0.01902,0.03918],"tcp_to_object_dist_end":0.01223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47605,-0.01906,0.02556],"object_pos_start":[0.47606,-0.01906,0.02559],"object_to_goal_dist_end":0.28803,"object_to_goal_dist_start":0.28801,"object_z_max":0.02559,"peak_contact_force":0.26542,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":44.0,"raw_peak_contact_force":0.26542,"tcp_end":[0.46526,-0.01887,0.03134],"tcp_start":[0.46528,-0.01887,0.03136],"tcp_to_object_dist_end":0.01224,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```