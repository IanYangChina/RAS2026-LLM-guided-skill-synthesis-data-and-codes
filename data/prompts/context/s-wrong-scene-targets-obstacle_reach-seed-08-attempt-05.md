## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | -0.1000 | 0.00 | ❌ rejected |
| 4 | approach | linear_cartesian | position_control | pose_tolerance | 1 | -0.0500 | 0.00 | ❌ rejected |
| 3 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | -0.1000 | 0.00 | ❌ rejected |
| 2 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | -0.1000 | 0.00 | ❌ rejected |
| 1 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | 0.1925 | 0.29 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`
- Frozen task target: [0.35, 0.0, 0.32]
- Goal object position: (0.35, 0.0, 0.32)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.6826972276605561, 0.048727684333792556, 0.15)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.6826972276605561, 0.048727684333792556, 0.15]
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
  frozen_task_target: [0.6827, 0.0487, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.35, 0.0, 0.32]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position (0.35, 0.0, 0.32) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.15) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.100) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: approach_above
  anchor: world
  offset:
  - 0.5
  - 0.0
  - 0.35
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_above_obstacle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: add
  guards:
  - id: above_obstacle
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.05
    - 0.0
  subtask_id: approach_above
- id: descend_to_goal
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
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: goal_reached
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
    - 0.02
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_obstacle** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (add)
  - guards:
    - id=above_obstacle, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.05, 0.0]
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=goal_reached, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.02, 0.02]

## Design Metrics

- **Composite score**: -0.100
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.100

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_clear | 0.00 | 0.00 | 0.0000 |
| descend_to_goal | 0.00 | 0.67 | 0.0372 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_clear | approach | 0.00 / guard_failure | (0.350, -0.000, 0.321)→(0.350, -0.000, 0.321) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_to_goal | descend | 0.00 / step_budget | (0.608, -0.007, 0.304)→(0.613, -0.016, 0.332) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.738→0.738 | 0.67 / 0.667 | 218.426 | 794.692 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.712
- path_efficiency: 0.487
- arc_smoothness: 0.974
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 926.525 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.226
- min_tcp_distance: 0.130
- tcp_proximity_score: 0.222
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link5
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.100
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.282


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `153111e21f17c0d331b561f1147684993204f9f696925b5b61ee34d65508a2ad`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `09a48f578e6b1d8164588605561432222dd1ada27be56833f7098561f0a0705c`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.6827,0.04873,0.15]},{"name":"goal","value":[0.5,0.0,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":23.0,"average_failure_rate":0.2987,"average_mean_iterations":64.03896,"average_solve_count":77.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clear.arc_height":0.1746,"descend_to_goal.speed":0.23483},"optimized_scores":{"best_composite_score":-0.1,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":164.0,"contact_point_centroid":[0.49724,-0.03286,0.29965],"force_p95":717.50024,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":926.52455,"mean_force":388.29992,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61339,0.03441,0.31047]},{"body_a":"obstacle_block","body_b":"link7","contact_count":578.0,"contact_point_centroid":[0.47597,0.01681,0.2999],"force_p95":381.9903,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":616.53163,"mean_force":300.83273,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.43523,0.01531,0.32514]},{"body_a":"obstacle_block","body_b":"link6","contact_count":293.0,"contact_point_centroid":[0.53746,0.02319,0.29988],"force_p95":380.21618,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":526.13796,"mean_force":283.77043,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.46225,0.02286,0.36653]}],"total_contact_groups":3},"final_pose_error":0.22586,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.63082,0.00243,0.36489],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":926.52455,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_clear","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1372.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":345.66745,"phase_name":"descend_to_goal","phase_peak_obstacle_force":926.52455,"phase_type":"descend","raw_contact_event_count":1035.0,"raw_peak_contact_force":926.52455,"subtask_id":"reach_goal","tcp_end":[0.63082,0.00243,0.36489],"tcp_start":[0.62864,0.02268,0.35855],"tcp_to_object_dist_end":0.72876,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e48c638882a658e374f83b9ad4d96930956de0db1e88d759e02d159e310d1b19`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.73702,-0.02132,0.15]},{"name":"goal","value":[0.5,0.0,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":27.0,"average_failure_rate":0.33333,"average_mean_iterations":71.40741,"average_solve_count":81.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clear.arc_height":0.18724,"descend_to_goal.speed":0.22572},"optimized_scores":{"best_composite_score":-0.1,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":309.0,"contact_point_centroid":[0.5398,0.08279,0.29961],"force_p95":649.78206,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":851.65963,"mean_force":255.3343,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59769,-0.01935,0.31408]},{"body_a":"obstacle_block","body_b":"link7","contact_count":533.0,"contact_point_centroid":[0.46954,-0.00588,0.2999],"force_p95":411.49165,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":560.86055,"mean_force":292.02881,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.4278,-0.00515,0.32439]},{"body_a":"obstacle_block","body_b":"link6","contact_count":277.0,"contact_point_centroid":[0.5381,-0.01361,0.29987],"force_p95":402.06047,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":540.92323,"mean_force":279.19083,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.46451,-0.00838,0.36623]}],"total_contact_groups":3},"final_pose_error":0.28234,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.60862,-0.02691,0.40138],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":851.65963,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_clear","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1307.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":309.61169,"phase_name":"descend_to_goal","phase_peak_obstacle_force":851.65963,"phase_type":"descend","raw_contact_event_count":1119.0,"raw_peak_contact_force":851.65963,"subtask_id":"reach_goal","tcp_end":[0.60862,-0.02691,0.40138],"tcp_start":[0.59926,-0.01951,0.31727],"tcp_to_object_dist_end":0.72955,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7c770227bfbc61ad3e08c75d3630762494b918d2814b704b39c653a43064979c`; realized-scene SHA-256: `61ec300895503e484321052c14122005b6d825b54245a4a918a581ea2f04a59f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.7456,-0.02923,0.15]},{"name":"goal","value":[0.5,0.0,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":36.0,"average_failure_rate":0.49315,"average_mean_iterations":101.05479,"average_solve_count":73.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clear.arc_height":0.18612,"descend_to_goal.speed":0.30709},"optimized_scores":{"best_composite_score":-0.1,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":185.0,"contact_point_centroid":[0.5382,-0.01635,0.29987],"force_p95":400.16381,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":605.89067,"mean_force":289.95074,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.46749,-0.01104,0.36334]},{"body_a":"obstacle_block","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.46822,-0.00809,0.29987],"force_p95":440.6145,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":572.359,"mean_force":304.30605,"phase_index":1.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.42786,-0.00669,0.32394]}],"total_contact_groups":2},"final_pose_error":0.16776,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.59862,-0.02296,0.23062],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":605.89067,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_clear","tcp_end":[0.35024,-0.0,0.32078],"tcp_start":[0.35027,-0.0,0.32082],"tcp_to_object_dist_end":0.47494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":838.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":605.89067,"phase_type":"descend","raw_contact_event_count":588.0,"raw_peak_contact_force":605.89067,"subtask_id":"reach_goal","tcp_end":[0.59862,-0.02296,0.23062],"tcp_start":[0.59696,-0.02282,0.23556],"tcp_to_object_dist_end":0.64192,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```