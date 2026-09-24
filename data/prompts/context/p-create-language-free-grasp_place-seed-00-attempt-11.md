## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5019 | 0.89 | ✅ accepted |
| 10 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4064 | 0.70 | ❌ rejected |
| 9 | approach → approach → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5307 | 0.75 | ✅ accepted |
| 8 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1620 | 0.33 | ✅ accepted |
| 7 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2605 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
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
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.888, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=0.502) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: none
  subtask_id: reach_object
- id: descend_to_grasp
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  guards:
  - id: contact_detected
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.18
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: move_to_goal
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
    - 0.1
    orientation:
      mode: none
  parameters:
    goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    move_speed:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
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
    - 0.02
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings: none
- **descend_to_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=contact_detected, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.18]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - goal_offset_z: status=consumed; consumers=target.offset.z (replace)
    - move_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.502
- **task_score** (E): 0.888
- **fitness_score**: 0.922  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1655 |
| descend_to_grasp | 1.00 | 1.00 | 0.1043 |
| grasp | 1.00 | 1.00 | 0.0124 |
| lift | 0.67 | 1.00 | 0.1247 |
| move_to_goal | 0.00 | 1.00 | 0.1125 |
| descend_to_place | 1.00 | 1.00 | 0.0998 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.001, 0.139) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.493, 0.001, 0.139)→(0.492, 0.001, 0.034) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.492, 0.001, 0.034)→(0.483, 0.000, 0.025) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.333 | 0.146 | 0.190 |
| lift | lift | 0.67 / step_budget | (0.483, 0.000, 0.025)→(0.479, 0.000, 0.150) | (0.497, 0.000, 0.026)→(0.491, 0.000, 0.138) | 0.266→0.222 | 1.00 / 32.000 | 0.093 | 0.680 |
| move_to_goal | approach | 0.00 / step_budget | (0.479, 0.000, 0.150)→(0.525, 0.085, 0.200) | (0.491, 0.000, 0.138)→(0.532, 0.086, 0.181) | 0.222→0.118 | 1.00 / 29.000 | 0.097 | 0.147 |
| descend_to_place | descend | 1.00 / step_budget | (0.525, 0.085, 0.200)→(0.570, 0.166, 0.203) | (0.532, 0.086, 0.181)→(0.574, 0.169, 0.177) | 0.118→0.023 | 1.00 / 20.667 | 0.129 | 0.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.376
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.718
- phase_breakdown.reach_goal_score: 0.652
- phase_breakdown.reach_object_score: 0.872
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.494
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.327


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
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56209,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.descend_speed":0.06774,"descend_to_place.place_z_offset":0.04543,"lift.lift_height":0.17127,"lift.lift_speed":0.05935,"move_to_goal.goal_offset_z":0.09369,"move_to_goal.move_speed":0.09504},"optimized_scores":{"best_composite_score":0.45413,"best_fitness_score":0.87413,"best_task_score":0.79345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.50904,-0.02207,-0.00113],"force_p95":0.46943,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6826,"mean_force":0.11621,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49745,-0.0225,0.02628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20527.0,"contact_point_centroid":[0.49663,-0.00349,0.07313],"force_p95":0.07622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29319,"mean_force":0.05047,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4949,-0.02245,0.07159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49568,-0.04163,0.07518],"force_p95":0.08094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29008,"mean_force":0.05887,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49489,-0.02245,0.07252]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51369,-0.02307,-0.00204],"force_p95":0.13775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17208,"mean_force":0.12616,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50068,-0.02256,0.02599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12742.0,"contact_point_centroid":[0.52563,0.10164,0.21247],"force_p95":0.12127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16592,"mean_force":0.07249,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52528,0.08259,0.21284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13920.0,"contact_point_centroid":[0.53075,0.06403,0.2114],"force_p95":0.10248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16365,"mean_force":0.06679,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52509,0.08208,0.21249]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.5137,-0.02302,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50317,-0.01028,0.2192]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50704,-0.02183,0.08574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.50047,-0.00348,0.02661],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10429,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15826.0,"contact_point_centroid":[0.5065,-0.00493,0.15814],"force_p95":0.08891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09817,"mean_force":0.06131,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50369,0.01397,0.1569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16827.0,"contact_point_centroid":[0.50492,0.0316,0.15612],"force_p95":0.08266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.05773,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50326,0.01267,0.15549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.4989,-0.0418,0.02758],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09217,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49943,-0.02253,0.02465]}],"total_contact_groups":12},"final_pose_error":0.04781,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54413,0.11942,0.21387],"final_tcp_position":[0.53859,0.11793,0.23729],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.6826,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50862,-0.02104,0.13838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50817,-0.02269,0.03408],"tcp_start":[0.50862,-0.02104,0.13838],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51355,-0.0229,0.02584],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26568,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13775,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.17208,"tcp_end":[0.49939,-0.02253,0.02461],"tcp_start":[0.50817,-0.02269,0.03408],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50624,-0.02306,0.11246],"object_pos_start":[0.51355,-0.0229,0.02584],"object_to_goal_dist_end":0.21169,"object_to_goal_dist_start":0.26568,"object_z_max":0.11235,"peak_contact_force":0.08198,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37722.0,"raw_peak_contact_force":0.6826,"tcp_end":[0.49505,-0.02245,0.12165],"tcp_start":[0.49939,-0.02253,0.02461],"tcp_to_object_dist_end":0.01449,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52249,0.04769,0.17677],"object_pos_start":[0.50624,-0.02306,0.11246],"object_to_goal_dist_end":0.1177,"object_to_goal_dist_start":0.21169,"object_z_max":0.1767,"peak_contact_force":0.08354,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32653.0,"raw_peak_contact_force":0.09817,"subtask_id":"reach_goal","tcp_end":[0.51499,0.04682,0.19314],"tcp_start":[0.49505,-0.02245,0.12165],"tcp_to_object_dist_end":0.01803,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54413,0.11942,0.21387],"object_pos_start":[0.52249,0.04769,0.17677],"object_to_goal_dist_end":0.0347,"object_to_goal_dist_start":0.1177,"object_z_max":0.21383,"peak_contact_force":0.15063,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26662.0,"raw_peak_contact_force":0.16592,"subtask_id":"reach_goal","tcp_end":[0.53859,0.11793,0.23729],"tcp_start":[0.51499,0.04682,0.19314],"tcp_to_object_dist_end":0.02411,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6443,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.descend_speed":0.07895,"descend_to_place.place_z_offset":0.02232,"lift.lift_height":0.13856,"lift.lift_speed":0.05914,"move_to_goal.goal_offset_z":0.07903,"move_to_goal.move_speed":0.12079},"optimized_scores":{"best_composite_score":0.55781,"best_fitness_score":0.97781,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.49662,0.04202,-0.00126],"force_p95":0.47017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67651,"mean_force":0.11837,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48527,0.04318,0.02699]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.48328,0.06217,0.07605],"force_p95":0.0838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29939,"mean_force":0.0588,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48281,0.04297,0.07332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20747.0,"contact_point_centroid":[0.48495,0.02405,0.07377],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28411,"mean_force":0.04975,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48281,0.04297,0.07237]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.0449,-0.00215],"force_p95":0.16684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2361,"mean_force":0.13431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4885,0.04348,0.02644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.48914,0.02439,0.02654],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1906,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48726,0.04337,0.02515]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16327.0,"contact_point_centroid":[0.54488,0.17193,0.15957],"force_p95":0.08355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17446,"mean_force":0.05951,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53691,0.18908,0.16087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13000.0,"contact_point_centroid":[0.53497,0.2094,0.16291],"force_p95":0.09483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14634,"mean_force":0.07125,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53753,0.19051,0.16087]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49753,0.02011,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49519,0.04252,0.08568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18656.0,"contact_point_centroid":[0.50395,0.07457,0.14292],"force_p95":0.08118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12059,"mean_force":0.05306,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49957,0.09298,0.14282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15643.0,"contact_point_centroid":[0.49874,0.11173,0.14509],"force_p95":0.08924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11234,"mean_force":0.06154,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49944,0.09265,0.14265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.4875,0.06271,0.02786],"force_p95":0.08398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09948,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48727,0.04337,0.02515]}],"total_contact_groups":12},"final_pose_error":0.01764,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56042,0.23526,0.13988],"final_tcp_position":[0.55557,0.23182,0.16117],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.67651,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49718,0.04114,0.13802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49587,0.04414,0.03423],"tcp_start":[0.49718,0.04114,0.13802],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04385,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24315,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16357,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11040.0,"raw_peak_contact_force":0.2361,"tcp_end":[0.48724,0.04336,0.02512],"tcp_start":[0.49587,0.04414,0.03423],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.04387,0.11283],"object_pos_start":[0.50116,0.04385,0.02548],"object_to_goal_dist_end":0.21573,"object_to_goal_dist_start":0.24315,"object_z_max":0.11273,"peak_contact_force":0.08055,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37947.0,"raw_peak_contact_force":0.67651,"tcp_end":[0.48296,0.04298,0.12242],"tcp_start":[0.48724,0.04336,0.02512],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5255,0.14224,0.14992],"object_pos_start":[0.49379,0.04387,0.11283],"object_to_goal_dist_end":0.10981,"object_to_goal_dist_start":0.21573,"object_z_max":0.14989,"peak_contact_force":0.09291,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34299.0,"raw_peak_contact_force":0.12059,"subtask_id":"reach_goal","tcp_end":[0.51843,0.13958,0.166],"tcp_start":[0.48296,0.04298,0.12242],"tcp_to_object_dist_end":0.01777,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56042,0.23526,0.13988],"object_pos_start":[0.5255,0.14224,0.14992],"object_to_goal_dist_end":0.01248,"object_to_goal_dist_start":0.10981,"object_z_max":0.14992,"peak_contact_force":0.09797,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29327.0,"raw_peak_contact_force":0.17446,"subtask_id":"reach_goal","tcp_end":[0.55557,0.23182,0.16117],"tcp_start":[0.51843,0.13958,0.166],"tcp_to_object_dist_end":0.0221,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89437,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.descend_speed":0.08951,"descend_to_place.place_z_offset":0.02607,"lift.lift_height":0.19268,"lift.lift_speed":0.12185,"move_to_goal.goal_offset_z":0.09781,"move_to_goal.move_speed":0.1367},"optimized_scores":{"best_composite_score":0.49381,"best_fitness_score":0.91381,"best_task_score":0.86982},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.47303,-0.01963,-0.00118],"force_p95":0.48602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67948,"mean_force":0.11771,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46128,-0.0197,0.02793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14956.0,"contact_point_centroid":[0.46249,-0.00099,0.10206],"force_p95":0.10163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30156,"mean_force":0.06371,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45887,-0.01965,0.10109]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12648.0,"contact_point_centroid":[0.46143,-0.03869,0.10447],"force_p95":0.11122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29433,"mean_force":0.07294,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45888,-0.01965,0.10256]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13260.0,"contact_point_centroid":[0.58261,0.13072,0.2204],"force_p95":0.10854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28001,"mean_force":0.07035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58267,0.1126,0.2206]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9369.0,"contact_point_centroid":[0.58729,0.09222,0.21835],"force_p95":0.15593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25109,"mean_force":0.10528,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57994,0.1098,0.2215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11848.0,"contact_point_centroid":[0.5076,0.00918,0.22049],"force_p95":0.11355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22321,"mean_force":0.08007,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50206,0.02757,0.22199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12433.0,"contact_point_centroid":[0.50777,0.0473,0.22245],"force_p95":0.1039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20158,"mean_force":0.0756,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.503,0.02857,0.2224]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02019,-0.00203],"force_p95":0.1352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16116,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01974,0.02758]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48643,-0.00894,0.21997]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47145,-0.01908,0.08667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.46409,-0.00068,0.02795],"force_p95":0.06872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10387,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4160.0,"contact_point_centroid":[0.46211,-0.03897,0.02884],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46283,-0.01972,0.0264]}],"total_contact_groups":12},"final_pose_error":0.02002,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61711,0.15086,0.17724],"final_tcp_position":[0.61659,0.14693,0.21055],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.67948,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47429,-0.01836,0.13938],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47123,-0.01986,0.0347],"tcp_start":[0.47429,-0.01836,0.13938],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.02008,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2885,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1352,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11034.0,"raw_peak_contact_force":0.16116,"tcp_end":[0.4628,-0.01972,0.02637],"tcp_start":[0.47123,-0.01986,0.0347],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":926.0,"n_steps_budget":990.0,"object_pos_end":[0.47422,-0.02015,0.18826],"object_pos_start":[0.47602,-0.02008,0.02587],"object_to_goal_dist_end":0.23849,"object_to_goal_dist_start":0.2885,"object_z_max":0.18813,"peak_contact_force":0.11726,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27747.0,"raw_peak_contact_force":0.67948,"tcp_end":[0.45953,-0.01966,0.20588],"tcp_start":[0.4628,-0.01972,0.02637],"tcp_to_object_dist_end":0.02294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5468,0.06955,0.21631],"object_pos_start":[0.47422,-0.02015,0.18826],"object_to_goal_dist_end":0.12605,"object_to_goal_dist_start":0.23849,"object_z_max":0.21629,"peak_contact_force":0.11535,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24281.0,"raw_peak_contact_force":0.22321,"subtask_id":"reach_goal","tcp_end":[0.54102,0.06803,0.23955],"tcp_start":[0.45953,-0.01966,0.20588],"tcp_to_object_dist_end":0.024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61711,0.15086,0.17724],"object_pos_start":[0.5468,0.06955,0.21631],"object_to_goal_dist_end":0.02092,"object_to_goal_dist_start":0.12605,"object_z_max":0.21631,"peak_contact_force":0.13898,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22629.0,"raw_peak_contact_force":0.28001,"subtask_id":"reach_goal","tcp_end":[0.61659,0.14693,0.21055],"tcp_start":[0.54102,0.06803,0.23955],"tcp_to_object_dist_end":0.03355,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```